<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xsl:output method="xml" indent="yes" />
    <xsl:param name="root" />
    <xsl:param name="codee-root" />
    <xsl:include href="../CommonXsltTemplates.xslt"/>
    <xsl:param name="exclude-collections" select="'false'" />
    <xsl:param name="relationship-suffix" select="''" />
    <xsl:variable name="airtable" select="/" />
    <xsl:variable name="squot">'</xsl:variable>
    <xsl:variable name="init-space">             </xsl:variable>
    <xsl:include href="GnfCommon.xslt"/>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <FileSet>

            <FileSetFile>
                    <xsl:element name="RelativePath"><xsl:text>../../../../src/gwbase/named_types/asl_types.py</xsl:text></xsl:element>

                <OverwriteMode>Always</OverwriteMode>
                <xsl:element name="FileContents">
<xsl:text>""" List of all the types used by the actor."""

from typing import Dict, List

from gw.named_types import GwBase
</xsl:text>
<xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')]">
<xsl:sort select="VersionedTypeName" data-type="text"/>
<xsl:variable name="versioned-type-id" select="VersionedType"/>
<xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending') and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">

<xsl:text>
from gwbase.named_types.</xsl:text>
<xsl:value-of select="translate(TypeName,'.','_')"/>
<xsl:text> import </xsl:text>
<xsl:call-template name="nt-case">
    <xsl:with-param name="type-name-text" select="TypeName" />
</xsl:call-template>
</xsl:for-each>
</xsl:for-each>
<xsl:text>

TypeByName: Dict[str, GwBase] = {}


def types() -> List[GwBase]:
    return [
        </xsl:text>
<xsl:for-each select="$airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase') and (normalize-space(VersionedTypeName)!='')]">
<xsl:sort select="VersionedTypeName" data-type="text"/>
<xsl:variable name="versioned-type-id" select="VersionedType"/>
<xsl:for-each select="$airtable//VersionedTypes/VersionedType[(VersionedTypeId = $versioned-type-id)  and (Status = 'Active' or Status = 'Pending')  and (ProtocolCategory = 'Json' or ProtocolCategory = 'GwAlgoSerial')]">
<xsl:call-template name="nt-case">
    <xsl:with-param name="type-name-text" select="TypeName" />
</xsl:call-template>
</xsl:for-each>


<xsl:choose>
 <xsl:when test="position() != count($airtable//ProtocolTypes/ProtocolType[(normalize-space(ProtocolName) ='gwbase')])">
<xsl:text>,
        </xsl:text>
</xsl:when>
<xsl:otherwise>
<xsl:text>,
    </xsl:text>
</xsl:otherwise>
</xsl:choose>
</xsl:for-each>
    <xsl:text>]


for t in types():
    try:
        TypeByName[t.type_name_value()] = t
    except Exception as e:
        print(f"Problem w {t}")
</xsl:text>



                </xsl:element>
            </FileSetFile>


        </FileSet>
    </xsl:template>


</xsl:stylesheet>
